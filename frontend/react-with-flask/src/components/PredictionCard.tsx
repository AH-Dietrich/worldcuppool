export type PredictionCardProps = {
    away: SideInfo,
    home: SideInfo,
    data: MatchInfo,
}

type MatchInfo = {
    stadium: string,
    time: string,
}

type SideInfo = {
    abbr: string,
    name: string,
    pic_url: string,
}

export const PredictionCard = (props: PredictionCardProps) => {
    return (<div>
        <button>
            <img src={props.home.pic_url} />
            <div>{props.home.name}</div>
        </button>
        OR
        <button>
            <img src={props.away.pic_url} />
            <div>{props.away.name}</div>
        </button>
    </div>)
}